module kind
implicit none
contains
subroutine real_kind(p, r, kind_value)
  integer, intent(in), optional :: p, r
  integer, intent(out) :: kind_value

  if(present(p).and.present(r)) then
    kind_value = selected_real_kind(p=p, r=r)
  else
    if (present(r)) then
      kind_value = selected_real_kind(r=r)
    else
      if (present(p)) then
        kind_value = selected_real_kind(p)
      endif
    endif
  endif
end subroutine real_kind

subroutine int_kind(p, r, kind_value)
  integer, intent(in), optional :: p, r
  integer, intent(out) :: kind_value

  if(present(p).and.present(r)) then
    kind_value = selected_int_kind(p)
  else
    if (present(r)) then
      kind_value = selected_int_kind(r=r)
    else
      if (present(p)) then
        kind_value = selected_int_kind(p)
      endif
    endif
  endif
end subroutine int_kind

end module kind
